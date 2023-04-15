"""
The metrics:
c_p: how much the product detail is related to the buyer's need
c_rw: how much a review is related to a buyer's need
c_u: how much a user is related to a buyer's figure

r_p_avg: average rating of a product


If a user only provide figure information:
find 4 most related user, and each user's highest's score product, return link

If a user only provide description of product:
find highest 5 c_p product

If a user provide both:
find highest 20 c_p product, and caculate the summed average of review
the weight is based on how much a user figure is related to the buyer,
then select 5 highest score product
"""