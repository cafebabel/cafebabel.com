from cafebabel import create_app, register_cli

app = create_app('config.BaseConfig')
register_cli(app)
