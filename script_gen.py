from trip.image_search import generate_vlog
import time

now = int(time.time())

a = now - 86400
b = now

generate_vlog(a, b)