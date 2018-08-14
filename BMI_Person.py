import json


class Person:
    def __init__(self, first_name="", last_name="", age=0, height=0, weight=0):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.height = height
        self.weight = weight
        self.bmi = self.__bmi(self.weight, self.height)
        self.bmi_category = self.__bmi_category(self.bmi)
        self.max_weight = self.get_max_weight()
        self.min_weight = self.get_min_weight()
        self.optimal_weight = ((self.max_weight - self.min_weight) / 2) + self.min_weight

    @staticmethod
    def __bmi(weight, height):
        a = (weight / height**2) * 703
        b = round(a, 1)
        return b

    @staticmethod
    def __bmi_category(bmi):
        if bmi <= 15:
            return "Very severely underweight"
        elif bmi >= 15 and bmi <= 16:
            return "Severely underweight"
        elif bmi >= 16 and bmi <= 18.5:
            return "Underweight"
        elif bmi > 18.5 and bmi <= 25:
            return "Normal"
        elif bmi > 25 and bmi <= 30:
            return "Overweight"
        else:
            return "Severely overweight"

    def print_json(self):
        print(json.dumps(self.__dict__))

    def print_bmi_data(self):
        text = 'Your BMI is {0} and you are considered {1}.'\
            .format(self.bmi, self.bmi_category.lower())
        print(text)
        if self.bmi_category == "Normal":
            if self.optimal_weight > self.weight:
                print('You are normal but just below optimal.')
            elif self.optimal_weight < self.weight:
                print('You are normal but just above optimal.')
        return 'Your min weight is {0} and your max weight is {1}'.format(self.min_weight, self.max_weight)

    def get_min_weight(self):
        for x in range(self.weight+100):
            y = self.__bmi_category(self.__bmi(x, self.height))
            if y == "Normal":
                return x

    def get_max_weight(self):
        for x in range(self.weight+100):
            y = self.__bmi_category(self.__bmi(x, self.height))
            if y == "Overweight":
                return x - 1


Me = Person(height=70, weight=160)

data = Me.print_bmi_data()

print(data)
print(len(data))
print(Me.optimal_weight)
