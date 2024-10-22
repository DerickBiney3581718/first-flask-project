from datetime import datetime


def log_datetime(func):
    """decorator to log the time a function was called 

    Args:
        func (function): function to be called 
    """
    def wrapper(*args, **kwargs):
        print(
            f"Function: {func.__name__}\n started running at {datetime.now().strftime('%Y-%m-01 %H:%M:%S')}")
        print("-"*50)
        func(*args, **kwargs)

    return wrapper


@log_datetime
def daily_backup():
    print('Daily backup has finished')


daily_backup()
print(daily_backup.__name__)
print(daily_backup.__doc__)