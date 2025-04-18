from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class User(models.Model):
    username = models.CharField(max_length=50, unique=True, db_column='username')
    password = models.CharField(max_length=15, validators=[MinLengthValidator(8)], db_column='password')
    firstName = models.CharField(max_length=50, db_column='firstname')
    lastName = models.CharField(max_length=50, blank=True, null=True, db_column='lastname')
    emailID = models.EmailField(max_length=100, unique=True, null=True, blank=True, db_column='emailid')
    contactNo = models.CharField(max_length=15, unique=True, null=True, blank=True, db_column='contactno')
    dob = models.DateField(null=True, blank=True, db_column='dob')
    walletCash = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
        db_column='walletcash'
    )

    def clean(self):
        if not self.emailID and not self.contactNo:
            raise ValidationError("At least one contact method (email or contactNo) must be provided.")

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user'


class Admin(models.Model):
    firstName = models.CharField(max_length=50, db_column='firstname')
    lastName = models.CharField(max_length=50, blank=True, null=True, db_column='lastname')
    emailID = models.EmailField(max_length=100, unique=True, db_column='emailid')
    password = models.CharField(max_length=15, validators=[MinLengthValidator(8)], db_column='password')
    role = models.CharField(max_length=50, blank=True, null=True, db_column='role')

    def __str__(self):
        return self.emailID

    class Meta:
        db_table = 'admin'


class Organizer(models.Model):
    staff = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, db_column='staffid')
    username = models.CharField(max_length=50, unique=True, db_column='username')
    firstName = models.CharField(max_length=50, db_column='firstname')
    lastName = models.CharField(max_length=50, blank=True, null=True, db_column='lastname')
    emailID = models.EmailField(max_length=100, unique=True, db_column='emailid')
    contactNo = models.CharField(max_length=15, unique=True, db_column='contactno')
    password = models.CharField(max_length=15, validators=[MinLengthValidator(8)], db_column='password')
    organization = models.CharField(max_length=100, blank=True, null=True, db_column='organization')
    verificationStatus = models.BooleanField(default=False, db_column='verificationstatus')
    dateOfVerification = models.DateField(null=True, blank=True, db_column='dateofverification')

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'organizer'


class Venue(models.Model):
    name = models.CharField(max_length=255, db_column='name')
    street = models.CharField(max_length=255, db_column='street')
    city = models.CharField(max_length=100, db_column='city')
    state = models.CharField(max_length=100, db_column='state')
    pincode = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{5,10}$')], db_column='pincode')

    class Meta:
        db_table = 'venue'
        unique_together = ("name", "street", "city", "state", "pincode")

    def __str__(self):
        return f"{self.name}, {self.city}"


class Event(models.Model):
    eventName = models.CharField(max_length=100, db_column='eventname')
    ticketPrice = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
        db_column='ticketprice'
    )
    category = models.CharField(max_length=50, db_column='category')
    maxAttendees = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True, db_column='maxattendees')
    created_at = models.DateTimeField(auto_now_add=True, db_column='createdat')
    startDate = models.DateField(db_column='startdate')
    startTime = models.TimeField(db_column='starttime')
    endDate = models.DateField(db_column='enddate')
    endTime = models.TimeField(db_column='endtime')
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True, db_column='venueid')
    organizer = models.ForeignKey(Organizer, on_delete=models.SET_NULL, null=True, blank=True, db_column='organizerid')
    ticketsSold = models.IntegerField(default=0, db_column='ticketssold')
    status = models.CharField(max_length=50, default='Upcoming', db_column='status')

    def __str__(self):
        return self.eventName

    class Meta:
        db_table = 'event'


class Transaction(models.Model):
    PAYMENT_METHODS = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Wallet']
    STATUS_CHOICES = ['Processed', 'Error', 'Refunded']

    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, db_column='eventid')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='userid')
    method_of_payment = models.CharField(max_length=50, choices=[(m, m) for m in PAYMENT_METHODS], db_column='methodofpayment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)], db_column='amount')
    date_of_payment = models.DateTimeField(auto_now_add=True, db_column='dateofpayment')
    status = models.CharField(max_length=10, choices=[(s, s) for s in STATUS_CHOICES], default='Processed', db_column='status')

    class Meta:
        db_table = 'transaction'


class Complaint(models.Model):
    STATUS_CHOICES = ['Pending', 'In Progress', 'Resolved', 'Dismissed']
    CATEGORY_CHOICES = [
        'Event Issues', 'Ticketing Problems', 'App & Tech Issues',
        'Safety & Security', 'Service & Hospitality', 'Other'
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_column='eventid')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userid')
    staff = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, db_column='staffid')
    Created_At = models.DateTimeField(auto_now_add=True, db_column='createdat')
    Description = models.TextField(db_column='description')
    Status = models.CharField(max_length=50, choices=[(s, s) for s in STATUS_CHOICES], null=True, blank=True, db_column='status')
    Category = models.CharField(max_length=100, choices=[(c, c) for c in CATEGORY_CHOICES], db_column='category')

    class Meta:
        db_table = 'complaint'
        unique_together = ('user', 'event', 'Category')


class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_column='eventid')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userid')
    Rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, db_column='rating')
    Comments = models.TextField(blank=True, null=True, db_column='comments')
    Created_At = models.DateTimeField(auto_now_add=True, db_column='createdat')

    class Meta:
        db_table = 'feedback'
        unique_together = ('user', 'event')


class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='userid')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, db_column='eventid')
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, db_column='transactionid')

    class Meta:
        db_table = 'registration'



