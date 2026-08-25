// W5 audit_store.js -- L0 IndexedDB backend for coxswain_turns +
// coxswain_overrides. Mirrors coxswain/src/coxswain/persistence/store.py's
// lifecycle/eviction/schema-version semantics (§2.3/§2.5), sends durability
// only on transaction complete (FR-9), and reports aborts loudly (AC-17).

import { describe, expect, test } from "bun:test";

import {
  DB_NAME,
  DEFAULT_TURN_CAP,
  OPEN_TURN_HEADROOM,
  SCHEMA_VERSION,
  AuditStore,
  OpenTurnCapacityExceeded,
  ReadOnlyStoreError,
} from "../audit_store.js";
import { FakeIndexedDBFactory } from "./fake_indexeddb.js";

const T0_MS = 1_700_000_000_000;

/** Deterministic clock: each call advances one second (returns ms). */
function steppedClock(startMs = T0_MS) {
  let now = startMs;
  return () => (now += 1000);
}

const TURN_ID = "cx-1700000000000-k3x9qz";
const SESSION = "cx-sess-1700000000000-abcd1234";

function makeDecisionPayload(turnId = TURN_ID, disposition = "continue") {
  return {
    turn_id: turnId,
    session_id: SESSION,
    gate_seq: 0,
    cue: 0,
    category: "initial",
    disposition,
    payload_kind: "",
    card_revision: 0,
    ts: 1700000000,
    fingerprint_id: null,
    override_id: null,
  };
}

async function openedStore(extra = {}) {
  const idbFactory = new FakeIndexedDBFactory();
  const systemLines = [];
  const store = new AuditStore({
    idbFactory,
    nowMs: steppedClock(),
    onSystemLine: (line) => systemLines.push(line),
    ...extra,
  });
  await store.open();
  return { idbFactory, store, systemLines };
}

function writeRequest(kind, turnId, payload, writeId = 1) {
  return { type: "audit.write", write_id: writeId, kind, turn_id: turnId, payload };
}

// --- open + creation ---------------------------------------------------------

describe("open", () => {
  test("creates both object stores at database version SCHEMA_VERSION", async () => {
    const { store } = await openedStore();
    expect(store.mode).toBe("read_write");
    const db = store._db;
    expect(db.version).toBe(SCHEMA_VERSION);
    expect([...db.objectStoreNames].sort()).toEqual([
      "coxswain_overrides",
      "coxswain_turns",
    ]);
  });

  test("beginTurn persists durably and mirrors locally", async () => {
    const { store } = await openedStore();
    await store.beginTurn(TURN_ID, SESSION);
    // Durable truth: the record is IN the object store.
    const durable = store._db._stores.coxswain_turns[TURN_ID];
    expect(durable.state).toBe("open");
    expect(durable.schema_version).toBe(SCHEMA_VERSION);
  });

  test("abandon-on-load closes turns found open at init (§2.3)", async () => {
    const idbFactory = new FakeIndexedDBFactory();
    await idbFactory.__seed(DB_NAME, SCHEMA_VERSION, (db) => {
      db.createObjectStore("coxswain_turns", { keyPath: "turn_id" });
      db.createObjectStore("coxswain_overrides", { keyPath: "override_id" });
      db._stores.coxswain_turns[TURN_ID] = {
        schema_version: SCHEMA_VERSION,
        turn_id: TURN_ID,
        session_id: SESSION,
        state: "open",
        opened_at: 1699999999,
        closed_at: null,
        transcript: [],
        pending_intents: [],
        decisions: [],
        fingerprints: [],
        outcome: null,
      };
    });
    const store = new AuditStore({
      idbFactory,
      nowMs: steppedClock(),
      onSystemLine: () => {},
    });
    await store.open();
    const record = store.queryTurn(TURN_ID).turn;
    expect(record.state).toBe("abandoned");
    expect(record.closed_at).not.toBeNull();
  });
});

// --- FR-9: ack ONLY on transaction complete ------------------------------------

describe("FR-9 durability semantics", () => {
  test("the ack resolves strictly after tx.complete, never on request success", async () => {
    const { idbFactory, store } = await openedStore();
    await store.beginTurn(TURN_ID, SESSION);

    const markers = [];
    const db = store._db;
    const realTransaction = db.transaction.bind(db);
    db.transaction = (...args) => {
      const tx = realTransaction(...args);
      let completeHandler = null;
      Object.defineProperty(tx, "oncomplete", {
        configurable: true,
        get: () => completeHandler,
        set: (fn) => {
          completeHandler = (event) => {
            markers.push("tx.complete");
            return fn.call(tx, event);
          };
        },
      });
      return tx;
    };

    const pending = store.applyWriteRequest(
      writeRequest("decision", TURN_ID, { record: makeDecisionPayload() }, 41),
    );
    const result = await pending;
    markers.push("ack.resolved");

    expect(result).toEqual({ type: "audit.ack", write_id: 41 });
    expect(markers.indexOf("tx.complete")).toBeGreaterThanOrEqual(0);
    expect(markers.indexOf("tx.complete")).toBeLessThan(markers.indexOf("ack.resolved"));
    // And the write actually landed durably.
    expect(db._stores.coxswain_turns[TURN_ID].decisions).toHaveLength(1);
  });

  test("applyWriteRequest maps every supported write kind onto the aggregate", async () => {
    const { store } = await openedStore();
    await store.applyWriteRequest(
      writeRequest("begin_turn", TURN_ID, { session_id: SESSION }, 1),
    );

    await store.applyWriteRequest(
      writeRequest(
        "attach_intent",
        TURN_ID,
        { intent: { turn_id: TURN_ID, parsed_call: { name: "transfer" }, unresolved_slots: ["source"] } },
        2,
      ),
    );
    await store.applyWriteRequest(
      writeRequest("decision", TURN_ID, { record: makeDecisionPayload() }, 3),
    );
    await store.applyWriteRequest(
      writeRequest(
        "fingerprint",
        TURN_ID,
        {
          record: {
            fingerprint_id: `${TURN_ID}:0:fp`,
            turn_id: TURN_ID,
            gate_seq: 0,
            card_revision: 0,
            taken_at: 1700000000,
            concurrency_active: false,
            precondition_digest: "cafe",
          },
        },
        4,
      ),
    );
    await store.applyWriteRequest(
      writeRequest("override", TURN_ID, {
        record: {
          schema_version: SCHEMA_VERSION,
          override_id: `${TURN_ID}:3:ovr`,
          turn_id: TURN_ID,
          gate_seq: 3,
          cue: 3,
          justification: "operator confirmed",
          ts: 1700000001,
        },
      }),
    );
    await store.applyWriteRequest(
      writeRequest(
        "attach_outcome",
        TURN_ID,
        {
          outcome: {
            turn_id: TURN_ID,
            gate_seq: 4,
            status: "aborted_stale",
            detail: "drift",
            ts: 1700000002,
          },
        },
        5,
      ),
    );

    const joined = store.queryTurn(TURN_ID);
    expect(joined.turn.pending_intents).toHaveLength(1);
    expect(joined.turn.decisions).toHaveLength(1);
    expect(joined.turn.fingerprints).toHaveLength(1);
    expect(joined.turn.outcome.status).toBe("aborted_stale");
    expect(joined.turn.state).toBe("closed"); // §2.3: any outcome closes
    expect(joined.overrides).toHaveLength(1);
    expect(joined.overrides[0].override_id).toBe(`${TURN_ID}:3:ovr`);
  });

  test("an unknown write kind is rejected loudly, never silently ignored", async () => {
    const { store, systemLines } = await openedStore();
    await store.beginTurn(TURN_ID, SESSION);
    await expect(
      store.applyWriteRequest(writeRequest("self_destruct", TURN_ID, {}), 99),
    ).rejects.toThrow(/unknown write kind/i);
  });
});

// --- §2.3 eviction -------------------------------------------------------------

describe("retention (§2.3)", () => {
  test("FIFO eviction removes OLDEST CLOSED records only and never an open turn", async () => {
    const { store } = await openedStore({ turnCap: 3 });
    // t1..t4 closed oldest-first; tOpen stays open throughout.
    const ids = [];
    for (let i = 0; i < 4; i += 1) {
      const id = `cx-170000000010${i}-aaa00${i}`;
      await store.beginTurn(id, SESSION);
      await store.closeTurn(id);
      ids.push(id);
    }
    await store.beginTurn("cx-1700000000999-open01", SESSION);

    // Population settles at cap: each write evicted the OLDEST CLOSED record;
    // the open turn was never a victim.
    expect(store.turnCount).toBe(3);
    expect(store.getTurn("cx-1700000000999-open01")).not.toBeNull();
    // Oldest closed were evicted first (t0, t1 gone; t2, t3 remain).
    expect(store.getTurn(ids[0])).toBeNull();
    expect(store.getTurn(ids[1])).toBeNull();
    expect(store.getTurn(ids[2])).not.toBeNull();
    expect(store.getTurn(ids[3])).not.toBeNull();
  });

  test("cap may be exceeded transiently by open turns alone (§2.3)", async () => {
    const { store } = await openedStore({ turnCap: 2 });
    await store.beginTurn("cx-1700000000011-open0a", SESSION);
    await store.beginTurn("cx-1700000000012-open0b", SESSION);
    await store.beginTurn("cx-1700000000013-open0c", SESSION);
    expect(store.turnCount).toBe(3); // nothing evicted: all open
  });

  test(`open turns reaching cap+${OPEN_TURN_HEADROOM} refuse loudly (§2.3)`, async () => {
    const { store, systemLines } = await openedStore({ turnCap: 2 });
    const limit = 2 + OPEN_TURN_HEADROOM;
    for (let i = 0; i < limit; i += 1) {
      await store.beginTurn(`cx-170000000002${i}-bbb00${i}`, SESSION);
    }
    await expect(
      store.beginTurn("cx-1700000000099-one-too-many", SESSION),
    ).rejects.toBeInstanceOf(OpenTurnCapacityExceeded);
    expect(systemLines.some((l) => l.includes("pathological"))).toBe(true);
  });

  test("overrides are exempt from eviction and keep their turn_id (AC-7)", async () => {
    const { store } = await openedStore({ turnCap: 1 });
    await store.beginTurn(TURN_ID, SESSION);
    await store.applyWriteRequest(
      writeRequest("override", TURN_ID, {
        record: {
          schema_version: SCHEMA_VERSION,
          override_id: `${TURN_ID}:3:ovr`,
          turn_id: TURN_ID,
          gate_seq: 3,
          cue: 3,
          justification: "confirmed",
          ts: 1700000000,
        },
      }),
    );
    await store.closeTurn(TURN_ID);
    // Two more closed turns churn past cap 1, evicting TURN_ID's record.
    await store.beginTurn("cx-1700000000077-churn01", SESSION);
    await store.closeTurn("cx-1700000000077-churn01");
    await store.beginTurn("cx-1700000000078-churn02", SESSION);
    await store.closeTurn("cx-1700000000078-churn02");

    expect(store.getTurn(TURN_ID)).toBeNull(); // turn evicted
    const survivors = store.overridesForTurn(TURN_ID);
    expect(survivors).toHaveLength(1); // override survived WITH turn_id
    expect(survivors[0].turn_id).toBe(TURN_ID);
    // And it is still durably present in its own store.
    expect(store._db._stores.coxswain_overrides[`${TURN_ID}:3:ovr`]).toBeDefined();
  });

  test(`default cap is ${DEFAULT_TURN_CAP} like store.py`, () => {
    expect(DEFAULT_TURN_CAP).toBe(1000);
  });
});

// --- §2.5 schema versioning ------------------------------------------------------

describe("schema-version check at open (§2.5)", () => {
  test("a NEWER build's store opens READ-ONLY with a loud line naming both numbers", async () => {
    const systemLines = [];
    // Simulate a newer build having written the store: db version
    // SCHEMA_VERSION+1 with record bodies carrying that version.
    const idbFactory = new FakeIndexedDBFactory();
    await idbFactory.__seed(DB_NAME, SCHEMA_VERSION + 1, (db) => {
      db.createObjectStore("coxswain_turns", { keyPath: "turn_id" });
      db.createObjectStore("coxswain_overrides", { keyPath: "override_id" });
      db._stores.coxswain_turns[TURN_ID] = {
        schema_version: SCHEMA_VERSION + 1,
        turn_id: TURN_ID,
        session_id: SESSION,
        state: "closed",
        opened_at: 1699999990,
        closed_at: 1700000000,
        transcript: [],
        pending_intents: [],
        decisions: [],
        fingerprints: [],
        outcome: null,
      };
    });
    const store = new AuditStore({
      idbFactory,
      nowMs: steppedClock(),
      onSystemLine: (line) => systemLines.push(line),
    });
    await store.open();

    expect(store.mode).toBe("read_only");
    expect(store.statusMessage).toContain(`schema ${SCHEMA_VERSION + 1}`);
    expect(store.statusMessage).toContain(`understands ${SCHEMA_VERSION}`);
    expect(systemLines.length).toBeGreaterThan(0);

    // Readable + exportable (AC-21)...
    expect(store.queryTurn(TURN_ID).turn.turn_id).toBe(TURN_ID);
    const bundle = store.exportBundle();
    expect(Object.keys(bundle.turns)).toEqual([TURN_ID]);
    // ...but NO write is accepted.
    await expect(store.beginTurn("cx-1700000000424-fresh01", SESSION)).rejects.toBeInstanceOf(
      ReadOnlyStoreError,
    );
    expect(systemLines.join("\n")).toContain("newer build");
  });

  test("an OLDER build's record bodies degrade read-only too, without coercion", async () => {
    const idbFactory = new FakeIndexedDBFactory();
    const systemLines = [];
    await idbFactory.__seed(DB_NAME, SCHEMA_VERSION, (db) => {
      db.createObjectStore("coxswain_turns", { keyPath: "turn_id" });
      db.createObjectStore("coxswain_overrides", { keyPath: "override_id" });
      db._stores.coxswain_turns[TURN_ID] = {
        schema_version: SCHEMA_VERSION - 1,
        turn_id: TURN_ID,
        session_id: SESSION,
        state: "closed",
        opened_at: 1699999990,
        closed_at: 1700000000,
        transcript: [],
        pending_intents: [],
        decisions: [],
        fingerprints: [],
        outcome: null,
      };
    });
    const store = new AuditStore({
      idbFactory,
      nowMs: steppedClock(),
      onSystemLine: (line) => systemLines.push(line),
    });
    await store.open();

    expect(store.mode).toBe("read_only");
    expect(store.statusMessage).toContain(`schema ${SCHEMA_VERSION - 1}`);
    // No silent coercion: the record keeps ITS version.
    expect(store.queryTurn(TURN_ID).turn.schema_version).toBe(SCHEMA_VERSION - 1);
    await expect(
      store.applyWriteRequest(writeRequest("begin_turn", "cx-1700000000424-x12345", { session_id: SESSION })),
    ).rejects.toBeInstanceOf(ReadOnlyStoreError);
    expect(store.exportBundle()).toBeTruthy();
  });
});

// --- queries ---------------------------------------------------------------

describe("queries", () => {
  test("queryTurn joins turn + overrides in ONE call; unknown returns null", async () => {
    const { store } = await openedStore();
    await store.beginTurn(TURN_ID, SESSION);
    await store.applyWriteRequest(
      writeRequest("override", TURN_ID, {
        record: {
          schema_version: SCHEMA_VERSION,
          override_id: "ovr-1",
          turn_id: TURN_ID,
          gate_seq: 3,
          cue: 3,
          justification: "ok",
          ts: 1700000000,
        },
      }),
    );
    const joined = store.queryTurn(TURN_ID);
    expect(joined.turn.turn_id).toBe(TURN_ID);
    expect(joined.overrides.map((o) => o.override_id)).toEqual(["ovr-1"]);
    expect(store.queryTurn("cx-9999999999999-nope00")).toBeNull();
  });

  test("exportBundle matches store.py's self-describing L3 shape", async () => {
    const { store } = await openedStore();
    await store.beginTurn(TURN_ID, SESSION);
    const bundle = store.exportBundle();
    expect(bundle.exported_by_schema_version).toBe(SCHEMA_VERSION);
    expect(Object.keys(bundle.turns)).toEqual([TURN_ID]);
    expect(bundle.overrides).toEqual([]);
  });
});
