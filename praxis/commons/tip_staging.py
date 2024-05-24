

async def split_tips_along_columns(wells: list[Well]) -> list[list[Well]]:
  if not all(isinstance(well, Well) for well in wells):
    raise ValueError("Invalid well type.")
  columns = [(await parse_well_name(well))[0] for well in wells]
  return [[well for column, well in zip(columns, wells) if column == i] for i in \
    range(max(columns)+1)]