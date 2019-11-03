from harbor.provider.manager import provider_manager


class App:
    def __init__(self):
        pass

    def load(self):
        loaded_items = provider_manager.load()
        for i in loaded_items:
            print(i)
