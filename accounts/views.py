from django.http import HttpResponse
from django.shortcuts import render, redirect

from accounts.models import User, UserProfile
from accounts.utils import detectUser
from vendor.forms import VenderForm
from .forms import UserForm
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied



def registerUser(request):
    if request.user.is_authenticated:
       return redirect('dashboard')
    elif(request.method== 'POST'):
     form = UserForm(request.POST)
     if form.is_valid():
        # Create the user using the form
        # pass_word = form.cleaned_data['password']
        # user = form.save(commit= False)
        # user.role = User.CUSTOMER
        # user.set_password(pass_word)
        # user.save()

# Create the user using create_user method
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
        user.role = User.CUSTOMER
        user.save()
        messages.success(request,"Your account has been registered succesfully!")
        return redirect('registerUser')
    else:
        form = UserForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
    # if request.user.is_authenticated:
    #     messages.warning(request, 'You are already logged in!')
    #     return redirect('registerVendor')
   if request.user.is_authenticated:
       return redirect('dashboard')

   elif request.method == 'POST':
        # store the data and create the user
        form = UserForm(request.POST)
        v_form = VenderForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid:
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']
            # vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # Send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            # send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your account has been registered sucessfully! Please wait for the approval.')
            return redirect('registerVendor')
        else:
            print('invalid form')
            print(form.errors)
   
   else:
        form = UserForm()
        v_form = VenderForm()

        context = {
        'form': form,
        'v_form': v_form,
        }

   return render(request, 'accounts/registerVendor.html',context)


def login(request):
    if request.user.is_authenticated:
       return redirect('myAccount')

    elif(request.method == 'POST'):
        email =  request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email = email,password = password)
        if user is not None:
            auth.login(request,user)
            messages.success(request,'you have logged in successfuly')
            return redirect('myAccount')
        else:
            messages.error(request,'Invalid login credential')    
            return redirect('login')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)
@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    # orders = Order.objects.filter(user=request.user, is_ordered=True)
    # recent_orders = orders[:5]
    # context = {
    #     'orders': orders,
    #     'orders_count': orders.count(),
    #     'recent_orders': recent_orders,
    # }
    return render(request, 'accounts/custDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    # vendor = Vendor.objects.get(user=request.user)
    # orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('created_at')
    # recent_orders = orders[:10]

    # # current month's revenue
    # current_month = datetime.datetime.now().month
    # current_month_orders = orders.filter(vendors__in=[vendor.id], created_at__month=current_month)
    # current_month_revenue = 0
    # for i in current_month_orders:
    #     current_month_revenue += i.get_total_by_vendor()['grand_total']
    

    # # total revenue
    # total_revenue = 0
    # for i in orders:
    #     total_revenue += i.get_total_by_vendor()['grand_total']
    # context = {
    #     'orders': orders,
    #     'orders_count': orders.count(),
    #     'recent_orders': recent_orders,
    #     'total_revenue': total_revenue,
    #     'current_month_revenue': current_month_revenue,
    # }
    return render(request, 'accounts/vendorDashboard.html')



def logout(request):
    auth.logout(request)
    messages.info(request,"you have logged out successfuly")
    return redirect('login')

def dashboard(request):
    return render(request, 'accounts/dashboard.html')
