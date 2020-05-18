#!/usr/bin/env python3
import os, pathlib
os.chdir(pathlib.Path(__file__).parent)

from aiohttp import web
import socketio

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

async def index(request):
    """Serve the client-side application."""
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

#{baseRoom : {"tables": {roomName: {userID: displayName}}}}
all_parties = {}
# all_parties = {
#     'nei3meeX': {
#         'tables': {
#             'room1': {
#                 '1-1': 'Katy Davis',
#             },
#             'room2': {
#                 '2-1': 'Katy Davis',
#                 '2-2': 'Evan Davis',
#             },
#             'room3': {
#                 '3-1': 'Katy Davis',
#                 '3-2': 'Evan Davis',
#                 '3-3': 'Ben Davis',
#             },
#         },
#     },
# }

#{userID: (baseRoom, roomName)}
curr_rooms = {}
#{sid: userID}
sid_to_user = {}

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def req_attendees(sid, data):
    print("req_attendees ", data)
    baseRoom = data['baseRoom']
    sio.enter_room(sid, baseRoom)
    if baseRoom not in all_parties:
        return # no need to send empty event
    tables = []
    for room_name, people_dict in all_parties[baseRoom]["tables"].items():
        people = []
        for user_id, display_name in people_dict.items():
            people.append({"userID": user_id, "displayName": display_name})
        tables.append({"roomName": room_name, "people": people})
    await sio.emit('attendees', tables, room=sid)

@sio.event
async def join_room(sid, data):
    print("join_room ", data)
    newBaseRoom = data['baseRoom']
    newRoomName = data['roomName']
    userID = data['userID']
    unjoin_user(sid, userID, newBaseRoom)

    sid_to_user[sid] = userID
    sio.enter_room(sid, newBaseRoom)
    curr_rooms[userID] = (newBaseRoom, newRoomName)

    if newRoomName is not None:
        party = all_parties.setdefault(newBaseRoom, {"tables": {}})
        table = party["tables"].setdefault(newRoomName, {})
        table[userID] = data['displayName']

    await sio.emit('join_room', data, room=newBaseRoom)

@sio.event
async def disconnect(sid):
    print('disconnect ', sid)
    if sid not in sid_to_user:
        return
    user_id = sid_to_user[sid]
    if user_id in curr_rooms:
        base_room, _ = curr_rooms[user_id]
        await sio.emit('leave_party', {'userID': user_id}, room=base_room)
    unjoin_user(sid, user_id)
    del sid_to_user[sid]

def unjoin_user(sid, userID, newBaseRoom=None):
    if userID not in curr_rooms:
        return
    oldBaseRoom, oldRoomName = curr_rooms[userID]
    try:
        del all_parties[oldBaseRoom]["tables"][oldRoomName][userID]
        if len(all_parties[oldBaseRoom]["tables"][oldRoomName]) == 0:
            del all_parties[oldBaseRoom]["tables"][oldRoomName]
            if len(all_parties[oldBaseRoom]["tables"]) == 0:
                del all_parties[oldBaseRoom]
    except KeyError as ex:
        print(ex)
    if oldBaseRoom != newBaseRoom:
        sio.leave_room(sid, oldBaseRoom)

app.router.add_static('/static', 'static')
app.router.add_get('/', index)

if __name__ == '__main__':
    web.run_app(app, port=26614)