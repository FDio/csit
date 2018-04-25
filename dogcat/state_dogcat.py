from animal import Animal


class DogCat(Animal):

    def __init__(self, species):
        self.species = species

    def make_sound(self):
        if self.species == "dog":
            return self.bark()
        elif self.species == "cat":
            return self.meow()
        else:
            return None

    def bark(self):
        """For historic reasons, this method has to be named this way."""
        return "Woof, woof!"

    def meow(self):
        """For historic reasons, this method has to be named this way."""
        return "..."  # Cats do not meow on demand.
