class BrowserSessionStore:
    def __init__(self):
        self.store: dict[str, tuple] = {}  # maps session names to (browser, context, page)

    def has_session(self, session_name: str) -> bool:
        return session_name in self.store

    def get_session(self, session_name: str) -> tuple:
        if session_name in self.store:
            return self.store[session_name]
        else:
            raise KeyError(f"Session '{session_name}' not found in BrowserSessionStore")

    def set_session(self, session_name: str, browser, context, page):
        self.store[session_name] = (browser, context, page)

    def close_session(self, session_name: str):
        if session_name in self.store:
            browser, context, page = self.store[session_name]
            if page:
                page.close()
            if context:
                context.close()
            if browser:
                browser.close()
            del self.store[session_name]

    def close_all(self):
        for session_name in list(self.store.keys()):
            self.close_session(session_name)
