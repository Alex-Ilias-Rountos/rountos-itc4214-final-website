from django.shortcuts import render, redirect
from .forms import RegistrationForm

# Create your views here.
def registration(response):

    if response.method == "POST":
        form = RegistrationForm(response.POST)
        if form.is_valid():
            form.save()
            #Customer2.objects.create(user=user, name=user.username, email=user.email)
        return redirect("/")
    else:
        form = RegistrationForm()

    return render(response, "newuserreg/registration.html", {"form":form})