

def update_asg_capacity(asg, desired=None, minlimit=None, maxlimit=None):
    print("Current limits: %s:%s" % (asg.min_size, asg.max_size))
    print("Current desired capacity %s" % asg.desired_capacity)

    changed = False

    if not minlimit is None:
        if asg.min_size != minlimit:
            print("Updating min_size (set to %s)" % minlimit)
            asg.min_size = minlimit
            changed = True

    if not maxlimit is None:
        if asg.max_size != maxlimit:
            print("Updating max_size (set to %s)" % maxlimit)
            asg.max_size = maxlimit
            changed = True

    if not desired is None:
        if asg.desired_capacity != desired:
            print("Updating desired_capacity to %s" % desired)
            asg.desired_capacity = desired
            changed = True

    if changed:
        asg.update()
        print("Success")
    else:
        print("Nothing to update")
