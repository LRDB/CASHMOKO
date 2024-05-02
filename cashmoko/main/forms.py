from django import forms
from .models import Person

Bank_Choices = (
    ("Gcash", "Gcash"),
    ("BPI", "BPI"),
    ("BDO", "BDO"),
    ("Maya", "Maya"),
    ("Wallet", "Wallet"),
    #("Ipon", "Ipon"),
    ("None", "None"),
)


class CreateTransactionEntry(forms.Form):

    amount = forms.IntegerField(label="Amount")
    endBank = forms.ChoiceField(choices=Bank_Choices)

    def __init__(self, user, cat, *args, **kwargs):
        super(CreateTransactionEntry, self).__init__(*args, **kwargs)
        # Fetch categories available for the user
        user_categories = (
            Person.objects.filter(user=user).values_list(cat, flat=True).first()
        )
        if user_categories:
            # Get user categories keys and convert them to a list of tuples
            choices = [(key, key) for key in user_categories.keys()]
            # Append "Others" as the last option
            choices.append(("Others", "Others"))
        else:
            # If no categories available for the user, provide default choices with "Others" as the only option
            choices = [("Others", "Others")]

        self.fields["category"] = forms.ChoiceField(
            choices=choices,
            widget=forms.Select,
        )

class CreateIponTransactionEntry(CreateTransactionEntry):
    Ipon_Challenge = [("Ipon","Ipon")]
    endBank = forms.ChoiceField(choices=Ipon_Challenge)