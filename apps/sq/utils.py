from django.conf import settings
from django.db.models import Avg, Max, Min, Count
# Python standard
import math

# Generates a SQ line of best fit and returns a mid-point intercept
# Should only be called via calculate_SQ
#
# @param n, x, y, xx, xy
#   n, sumx, sumxx, sumy, sumxy
# @return
#   LOBF midpoint readoff (SQ)
def sq_lobf( n, x, y, xx, xy ):

    # Line of best fit: y = mx + b 5
    # See: http://people.hofstra.edu/stefan_waner/realworld/calctopic1/regression.html
    denominator = ( n * xx ) - ( math.pow( x, 2 ) )
    

    # Prevent divide by zero
    if denominator == 0:
        return 0

    m = ( ( n * xy ) - ( x * y ) ) / denominator
    b = ( y - ( m * x ) ) / n

    """
    Now we have our values we simply pop in the numbers and extract the SQ
    (approximation)
    y = %correct at given point - we assume SQ_READOFF_MARK
    x is the value we want
    x = ( y - b ) / m
    """

    # If we end up with an "infinite" SQ top-round it off
    # @xxx: This should not happen if we are pinning correctly. CHECK!
    if m == 0:
        return settings.SQ_UPPER_LIMIT

    sq = ( settings.SQ_READOFF_MARK - b ) / m
    # SQ Boundary Limits for realism.
    # @xxx: These should not be reached in reality (or *rarely*). CHECK!
    sq = max( sq, settings.SQ_LOWER_LIMIT );
    sq = min( sq, settings.SQ_UPPER_LIMIT );
    
    return int(sq);


# Calculates an SQ via lobf when passed a query returning X and Y values
#
# @param data
#   Data dict to be SQ calculated
# @return
#   Calculated SQ value
def sq_calculate( data, direction = 'asc' ):

    if data:
        pass
    else:
        return None # Default 'no data' value

    # Initialise (must do as n = n + )
    n = 0
    x = 0
    y = 0
    xx = 0
    xy = 0
    # Process summary values for each variable
    # COUNT(*) as n, SUM(x) AS sumx, SUM(y) AS sumy, SUM(POWER(x,2)) AS sumxx, SUM(x*y) AS sumxy FROM (' .
    for e in data:
        n  = n  + 1 #e['n']
        x  = x  + e['x']
        y  = y  + e['y']
        xx = xx + math.pow(e['x'],2)
        xy = xy + ( e['x'] * e['y'] )

    # Increase pin as numbers increase (x0.1 e.g.)
    # +1 so is pinned before data is added
    pin = 1+ ( e['n'] * settings.SQ_PINNING_WEIGHT )

    # NOTE: (x) SQ range 0-200, (y) Correct range 0-100

    if direction == 'asc': # Line goes bottom-left, to top right (e.g. qSQ)
        x  = x  + ( 200   * pin )
        y  = y  + ( 100   * pin )
        xx = xx + ( 40000 * pin )
        xy = xy + ( 20000 * pin )
        n  = n  + ( 2     * pin )
    elif direction == 'desc': # Line goes top-left, to bottom right (e.g. uSQ)
        x  = x  + ( 200   * pin )
        y  = y  + ( 100   * pin )
        xx = xx + ( 40000 * pin )
        xy = xy + ( 0     * pin )
        n  = n  + ( 2     * pin )
    #else No pinning   

    # Pass query result to lobf function, return SQ
    return round( sq_lobf( n, x, y, xx, xy ), 0 )
    
    
def sq_division(sq):

    if sq is None:
        return None
        
    # Limit SQ to the range 149-69
    sq = min( max( sq , 69  ) , 149 )
    # Convert to 14-6
    return int( math.floor( sq / 10) ) - 5 # Range 1-9


def sq_division_changed( sqa, sqb ):
    return sq_division( sqa ) != sq_division( sqb )

