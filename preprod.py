from cafebabel import create_app, register_cli

app = create_app('config.PreprodConfig')
register_cli(app)
