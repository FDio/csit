from animal import Animal


class Dog(Animal):

    def make_sound(self):
        return self.bark()

    def bark(self):
        """For historic reasons, this method has to be named this way."""
        return "Woof, woof!"


class Cat(Animal):

    def make_sound(self):
        return self.meow()

    def meow(self):
        """For historic reasons, this method has to be named this way."""
        return "..."  # Cats do not meow on demand.


# There is no class DogCat.
class DogCatFactory(object):

    @staticmethod
    def create_animal(species):
        """Return an animal object of the given species."""
        if self.species == "dog":
            return Dog()
        elif self.species == "cat":
            return Cat()
        else:
            return None
