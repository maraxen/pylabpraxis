from web_bridge import request_user_interaction


async def pause(message="Paused"):
  return await request_user_interaction("pause", {"message": message})


async def confirm(message):
  return await request_user_interaction("confirm", {"message": message})


async def input(prompt):
  return await request_user_interaction("input", {"prompt": prompt})
