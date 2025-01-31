


class Rider:

    def kill_bosh(self):
        if self.onSled:
            self.constraints = self.constraints[:-8]
            self.onSled = False

