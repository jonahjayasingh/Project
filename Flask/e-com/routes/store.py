from flask import Blueprint, render_template, abort
from models import User, UserType, Product, SellerProfile

routes = Blueprint('store', __name__)

@routes.route('/<string:username>')
def seller_store(username):
    seller = User.query.filter_by(username=username, user_type=UserType.SELLER).first_or_404()
    
    # Get products for this seller
    products = Product.query.filter_by(seller_id=seller.id).all()
    
    # Get seller profile details
    profile = seller.seller_profile
    
    return render_template('store/view.html', seller=seller, profile=profile, products=products)
