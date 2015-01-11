import math

K = 6. # The higher this is, the more effective is a single position to a user's rating.
KP = 260. # The higher this is, the higher the spread of the ratings between users.

# Chosen so that .05 eq_diff implies a .5 outcome and 0 eq_diff implies a 1 outcome:
a = - math.log(.5) / .05

def phi(x):
	'Cumulative distribution function for the standard normal distribution'
	return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def equity_diff_to_p(equity_diff):
	return math.exp(a * equity_diff)
	
def match_increment(player_rating, position_rating, eq_diff):
	""" Winner's rating comes first. """
	rdiff = player_rating - position_rating
	p_from_rating = phi(rdiff / KP)
	p_from_selection = equity_diff_to_p(eq_diff)
	surplus = p_from_selection - p_from_rating
	result = K * surplus
	return result
	
if __name__ == '__main__':
	for i in xrange(100):
		print match_increment(1500., 1500., .002)
