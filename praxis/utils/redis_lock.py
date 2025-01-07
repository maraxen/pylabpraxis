import redis
import time
import contextlib

@contextlib.contextmanager
def acquire_lock(redis_client: redis.Redis, resource_name: str, lock_timeout: int = 60, acquire_timeout: int = 10):
    """
    Acquires a lock on a resource using Redis.

    Args:
        redis_client: The Redis client instance.
        resource_name: The name of the resource to lock.
        lock_timeout: The duration of the lock in seconds.
        acquire_timeout: The maximum time to wait to acquire the lock (in seconds).

    Yields:
        True if the lock was acquired, False otherwise.

    Raises:
        Exception: If there was an error acquiring or releasing the lock.
    """
    lock_name = f"lock:{resource_name}"
    identifier = str(int(time.time()))  # Unique identifier for the lock

    end_time = time.time() + acquire_timeout
    acquired = False
    try:
        while time.time() < end_time:
            if redis_client.set(lock_name, identifier, ex=lock_timeout, nx=True):
                # Lock acquired
                acquired = True
                yield True
                return  # Exit the while loop and context manager
            time.sleep(0.1)  # Wait for a short time before retrying
        # Timeout
        yield False
    except Exception as e:
        print(f"Error acquiring or releasing lock: {e}")
        raise
    finally:
        # Only release the lock if it was acquired and the identifier matches
        if acquired and redis_client.get(lock_name).decode('utf-8') == identifier:
            try:
                redis_client.delete(lock_name)
            except Exception as e:
                print(f"Error releasing lock: {e}")
                raise


