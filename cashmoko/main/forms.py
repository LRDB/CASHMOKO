from django import forms

Bank_Choices =(
    ("Gcash", "Gcash"),
    ("BPI", "BPI"),
    ("BDO", "BDO"),
    ("Maya", "Maya"),
    ("Wallet", "Wallet"),
    ("Ipon", "Ipon"),
    ("None", "None"),
)

class CreateTransactionEntry(forms.Form):
    category = forms.CharField(label="Category", max_length=200)
    amount = forms.IntegerField(label="Amount")
    startBank = forms.ChoiceField(choices = Bank_Choices)
    endBank = forms.ChoiceField(choices = Bank_Choices)