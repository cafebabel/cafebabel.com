from cafebabel import create_app, register_cli

app = create_app('config.ProdConfig')
register_cli(app)
