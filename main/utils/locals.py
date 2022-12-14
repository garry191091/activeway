from main.models import Product, Venue


def find_replace_product_name(items):
    keyword = list(Product.objects.values_list("keyword", flat=True))
    output_data = None
    # This is the list of keywords
    for words in keyword:
        if words in items:
            output_data = words
    return output_data


def find_replace_venue_name(items):
    keyword = list(Venue.objects.values_list("keyword", flat=True))
    output_data = None
    # This is the list of keywords
    for words in keyword:
        if words in items:
            output_data = words
    return output_data
