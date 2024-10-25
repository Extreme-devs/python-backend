from trip.image_search import generate_blog
import time

now = int(time.time())
then = now - 3600 * 2

generate_blog(then, now)
