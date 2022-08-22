import pprint
from django.shortcuts import render
from django.views.generic import DetailView
from .models import AccountDeleteRequest

# Create your views here.

class AccountDeleteView(DetailView):
	queryset = AccountDeleteRequest.objects.filter(active=True)


	template_name = "accounts/delete_account.html"

	def post(self, request, *args, **kwargs):
		delete_btn = request.POST.get("delete_account", None)
		pprint.pprint(request.POST)
		context = {"message": "No Option Selected"}
		print("delete button is", delete_btn)
		obj = self.get_object()
		if delete_btn  == "complete-deletion":
			print("something happened here")
			obj.delete_user_account()
			context["message"] = "Account deleted"
			context["hide_buttons"] =  True
		# elif delete_btn == "cancel-deletion":
		# 	print("something happened  xxxx")
		# 	obj.user.is_active = True
		# 	obj.user.save()
		# 	obj.delete()
		# 	context["message"] = "Deletion Request Cancelled"
		# 	context["hide_buttons"] =  True
		return render(request, self.template_name, context)
