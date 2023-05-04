try:
    try:
        raise Exception("FUDEU")
        a, b = False
    except Exception as exc:
        print("First exc")
        # raise exc
except Exception as exc:
    print("Second exc")
    print(str(exc))
