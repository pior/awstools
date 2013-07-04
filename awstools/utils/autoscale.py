

def update_asg(asg,
               desired=None, minlimit=None, maxlimit=None):
    updated = []

    if not minlimit is None and asg.min_size != minlimit:
        asg.min_size = minlimit
        updated.append('min')

    if not maxlimit is None and asg.max_size != maxlimit:
        asg.max_size = maxlimit
        updated.append('max')

    if not desired is None and asg.desired_capacity != desired:
        asg.desired_capacity = desired
        updated.append('capacity')

    if updated:
        asg.update()

    return updated
