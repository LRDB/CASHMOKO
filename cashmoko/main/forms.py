from django import forms
from .models import Person


class BasisTransactionEntry(forms.Form):
    amount = forms.IntegerField(label="Amount")

    def __init__(self, user, *args, **kwargs):
        super(BasisTransactionEntry, self).__init__(*args, **kwargs)


class BankTransactionEntry(BasisTransactionEntry):
    def __init__(self, user, *args, **kwargs):
        super(BasisTransactionEntry, self).__init__(*args, **kwargs)
        user_banks = (
            Person.objects.filter(user=user).values_list("banks", flat=True).first()
        )
        if user_banks:
            choices = [(key, key) for key in user_banks.keys()]
        else:
            choices = [("None", "None")]

        self.fields["endBank"] = forms.ChoiceField(
            choices=user_banks, widget=forms.Select
        )


class CreateTransactionEntry(BasisTransactionEntry):
    def __init__(self, user, cat, *args, **kwargs):

        super(BasisTransactionEntry, self).__init__(*args, **kwargs)

        user_banks = (
            Person.objects.filter(user=user).values_list("banks", flat=True).first()
        )

        if user_banks:
            choices = [(key, key) for key in user_banks.keys()]
            choices.remove(("Ipon", "Ipon"))
        else:
            choices = [("None", "None")]

        self.fields["endBank"] = forms.ChoiceField(choices=choices, widget=forms.Select)

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


class BankTransferTransactionEntry(BasisTransactionEntry):
    def __init__(self, user, *args, **kwargs):

        super(BasisTransactionEntry, self).__init__(*args, **kwargs)

        user_banks = (
            Person.objects.filter(user=user).values_list("banks", flat=True).first()
        )
        if user_banks:
            choices = [(key, key) for key in user_banks.keys()]
        else:
            choices = [("None", "None")]

        self.fields["startBank"] = forms.ChoiceField(
            choices=user_banks, widget=forms.Select
        )

        self.fields["endBank"] = forms.ChoiceField(
            choices=user_banks, widget=forms.Select
        )


class CreateIponTransactionEntry(BasisTransactionEntry): ...
