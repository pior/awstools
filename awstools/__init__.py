import boto

_cfn = None
def cfn():
    """Helper for Cloudformation connection"""
    global _cfn
    if _cfn is None:
        _cfn = boto.connect_cloudformation()
    return _cfn


def find_stacks(pattern=None, findall=False):
    """Return a list of stacks matching a pattern"""
    stacks = cfn().list_stacks()

    if pattern:
        stacks = [s for s in stacks if pattern in s.stack_name]

    if not findall:
        INVALID_STATUS = ["DELETE_COMPLETE"]
        stacks = [s for s in stacks if s.stack_status not in INVALID_STATUS]

    return sorted(stacks, key=lambda k: k.stack_name)

def find_one_stack(pattern, findall=False, summary=True):
    """Return the result is there is only one. Raise ValueError otherwise"""
    stacks = find_stacks(pattern=pattern, findall=findall)

    for stack in stacks:        # If we have an exact match, just take it
        if stack.stack_name == pattern:
            stacks = [stack]
            break

    if len(stacks) > 1:
        raise ValueError("More than one stack matched this pattern: %s" % pattern)
    if len(stacks) == 0:
        raise ValueError("No stack found with pattern: %s" % pattern)
    if summary:
        return stacks[0]
    else:
        return cfn().describe_stacks(stacks[0].stack_name)[0]
