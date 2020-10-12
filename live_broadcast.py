from InstaLiveCLI import InstaLiveCLI

live = InstaLiveCLI(
    settings='auth.json'
)

a = live.create_broadcast()
# live.export_settings('auth.json')
# live.start_broadcast()
# live.live_info()
print(live.get_broadcast_status())
print(live.settings)

# start new
# live = InstaLiveCLI(
#     username='hanyadummy',
#     password='raihan123'
# )

# live.login()
# live.export_settings('auth.json')
# print(live.settings)