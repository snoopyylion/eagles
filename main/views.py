import uuid
import json
import requests


from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import logout,login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from .forms import *
from .models import *

# Create your views here.
def homepage(request):
    popular = Product.objects.filter(popular=True)
    featured = Product.objects.filter(featured=True)

    context = {
        'popular':popular,
        'featured':featured
    }
    
    return render(request, 'index.html', context)

def products(request):
    prod = Product.objects.all()
    p = Paginator(prod, 8)
    page = request.GET.get('page')
    pagin = p.get_page(page)


    context = {
        'pagin': pagin,
    }

    return render(request, 'product.html', context)

def category(request, id):
    catname = Category.objects.get(pk=id)
    catprod = Product.objects.filter(type_id=id)


    context = {
        'catname': catname,
        'catprod': catprod
    }
    return render(request, 'category.html', context)

def detail(request, id, slug):
    fdet = Product.objects.get(pk=id)
    fsize = Size.objects.all()

    context ={
        'fdet':fdet,
        'fsize':fsize,
    }

    return render(request, 'detail.html', context)


def search(request):
    if request.method=='POST':
        item = request.POST['item']
        search_item = Q(Q(name__icontains=item)|Q(description__icontains=item))
        search = Product.objects.filter(search_item)

        context={
            'search':search,
            'item':item
        }

        return render(request, 'search.html', context)

def contact(request):
    contact = ContactForm()
    if request.method == 'POST':
        contact = ContactForm(request.POST)
        if contact.is_valid():
            contact.save()
            messages.success(request, 'Your message is sent successfully')
            return redirect('home')
        


    context = {
        'contact':contact
    }

    return render(request, 'contact.html', context)

def signout(request):
    logout(request)
    messages.success(request, 'you are now loggedout')
    return redirect('signin')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'you are now signed in')
            return redirect('home')
        else:
            messages.info(request, 'username/password is incorrect')
            return redirect('signin')
    return render(request, 'signin.html')

def signup(request):
    customer = CustomerForm()
    if request.method == 'POST':
        phone = request.POST['phone']
        address = request.POST['address']
        pix = request.POST['pix']
        customer = CustomerForm(request.POST)
        if customer.is_valid():
            user = customer.save()
            newuser = Customer()
            newuser.user = user
            newuser.first_name = user.first_name
            newuser.last_name =  user.last_name
            newuser.email =  user.email
            newuser.phone =  phone
            newuser.address =  address
            newuser.pix =  pix
            newuser.save()
            messages.success(request, f'dear {user} account is created succesfully')
            return redirect('signin')
        else:
            messages.error(request, customer.errors)
            return redirect('signup')
        
    return render(request, 'signup.html')


@login_required(login_url='signin')
def profile(request):
    userprof = Customer.objects.get(user__username = request.user.username)

    context = {
        'userprof':userprof
    }

    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def profile_update(request):
    userprof =  Customer.objects.get(user__username=request.user.username)
    profile = ProfileUpdateForm(instance=request.user.customer)
    if request.method == 'POST':
        profile = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.customer)
        if profile.is_valid():
            pupdate = profile.save()
            new = pupdate.first_name.title()
            messages.success(request, f'dear {new} your profile update is successful')
            return redirect('profile')
        else:
            new = pupdate.first_name.title()
            messages.error(request, f'dear{new} your profile update generated the following errors: {profile.errors}')
            return redirect('profile_update')
        

    context = {
        'userprof': userprof
    }

    return render(request, 'profile_update.html', context)


@login_required(login_url='signin')
def password_update(request):
    userprof =  Customer.objects.get(user__username=request.user.username)
    passupdate = PasswordChangeForm(request.user)
    if request.method == 'POST':
        new = request.user.username.title()
        passupdate = PasswordChangeForm(request.POST, request.user)
        if passupdate:
            update_session_auth_hash(request, passupdate)
            messages.success(request, f'dear {new} your password is updated succesfully')
            return redirect('profile')
        else:
            messages.error(request, f'the following errors occured : {passupdate.errors}')
            return redirect('password_update')
    
    context = {
        'userprof':userprof,
        'passupdate':passupdate
    }

    return render(request, 'password_update.html', context)


@login_required(login_url='signin')
def add_to_cart(request):
    if request.method == 'POST':
        item = request.POST['itemid']
        quantity = int(request.POST['quantity'])
        
        product = Product.objects.get(pk=item)
        cart = Cart.objects.filter(user__username = request.user.username, paid=False)
        if cart:
            basket = Cart.objects.filter(user__username = request.user.username, product=product.id, price = product.price,  paid= False).first()
            if basket:
                basket.quantity += quantity
                basket.amount = product.price * basket.quantity
                basket.save()
                messages.success(request, 'one item added to cart')
                return redirect('home')
            else:
                newitem = Cart()
                newitem.user = request.user
                newitem.product = product
                newitem.price = product.price
                newitem.quantity = quantity
                newitem.amount = product.price * quantity
                newitem.paid = False
                newitem.save()
                messages.success(request,'one item added to cart')
                return redirect('home')
        else:
            newitem = Cart()
            newitem.user = request.user
            newitem.product = product
            newitem.price = product.price
            newitem.quantity = quantity
            newitem.amount = product.price * quantity
            newitem.paid = False
            newitem.save()
            messages.success(request,'one item added to cart')
            return redirect('home')


@login_required(login_url='signin')
def cart(request):
    cart = Cart.objects.filter(user__username = request.user.username, paid=False)
    for item in cart:
        item.amount = item.price * item.quantity
        item.save()

    subtotal = 0
    vat = 0
    total = 0

    for item in cart:
        subtotal += item.amount
        vat = 0.075 * subtotal
        total = subtotal + vat

    context = {
        'cart':cart,
        'subtotal': subtotal,
        'vat': vat,
        'total':total
    }

    return render(request, 'cart.html', context)

@login_required(login_url='signin')
def delete(request):
    if request.method == 'POST':
        delid = request.POST['delid']
        Cart.objects.get(pk=delid).delete()
        messages.success(request, 'item removed')
        return redirect('cart')
    
@login_required(login_url='signin')
def update(request):
    if request.method == 'POST':
        itemid = request.POST['itemid']
        quant = request.POST['quant']
        newquant = Cart.objects.get(pk=itemid)
        newquant.quantity = quant
        newquant.amount = newquant.price * newquant.quantity
        newquant.save()
        messages.success(request, 'quantity added')
        return redirect('cart')
    
@login_required(login_url='signin')
def checkout(request):
    userprof = Customer.objects.get(user__username = request.user.username)
    cart = Cart.objects.filter(user__username = request.user.username)
    for item in cart:
        item.amount = item.price * item.quantity
        item.save()

    subtotal = 0
    vat = 0
    total = 0

    for item in cart:
        subtotal += item.amount
        vat = 0.075 * subtotal
        total = subtotal + vat

    context = {
        'cart':cart,
        'userprof': userprof,
        'total':total
    }
    return render(request, 'checkout.html',context)

@login_required(login_url='signin')
def payment(request):
    if request.method == 'POST':
        profile = Customer.objects.get(user__username = request.user.username)
        api_key ='sk_test_1b3a8bddecae1ef79898ecfbd45591551d9e2be3' #secret key from paystack
        curl ='https://api.paystack.co/transaction/initialize' #paystack call url
        cburl = 'http://13.53.33.106/thankyou' #thank you page
        ref = str(uuid.uuid4()) #reference id required by paystack as an addiional reference number
        order_no = profile.id
        amount = float(request.POST['total']) * 100 #the total amount that would be charged
        email = profile.email
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        address = request.POST['address']
        phone = request.POST['phone']

        #collect data to send to paystack via call url
        headers = {'Authorization': f'Bearer {api_key}'}
        data = {'reference':ref, 'amount':int(amount), 'email':email, 'callback_url':cburl, 'order_number':order_no, 'currency':'NGN'}

        #Make a Call to Paystack
        try:
            r = requests.post(curl, headers=headers, json=data)
        except Exception:
            messages.error(request, 'network busy, try again later')
        else:
            transback = json.loads(r.text)
            rdurl = transback['data']['authorization_url']


            account = Order()
            account.user = profile.user
            account.first_name = first_name
            account.last_name = last_name
            account.phone = phone
            account.address = address
            account.amount = amount/100
            account.paid = True
            account.pay_code = ref
            account.save()

            return redirect(rdurl)
    return redirect('checkout')

@login_required(login_url='signin')
def thankyou(request):
    userprof = Customer.objects.get(user__username = request.user.username)
    cart = Cart.objects.filter(user__username = request.user.username, paid=False)

    for item in cart:
        item.paid=True
        item.save()

        product = Product.objects.get(pk=item.product.id)


    context ={
        'userprof':userprof,
        'cart':cart,
        'product':product
    }

    return render(request, 'callback.html', context)