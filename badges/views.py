from django.shortcuts import render

from .models import Badge


def get_badge_sort_order(badge):
    if badge.tier == 'bronze':
        tier_number = 1
    elif badge.tier == 'silver':
        tier_number = 2
    elif badge.tier == 'gold':
        tier_number = 3
    else:
        tier_number = 4

    return tier_number, badge.name


def badges_list_view(request):
    badges = list(Badge.objects.all())
    badges.sort(key=get_badge_sort_order)
    return render(request, 'badges/list.html', {'badges': badges})
