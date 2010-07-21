import re

from django.db.models import Q

class AddressSearch:

    def normalize_query(self, query_string,
    	                findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
    	                normspace=re.compile(r'\s{2,}').sub):
    	''' Splits the query string in invidual keywords, getting rid of unecessary spaces
    	    and grouping quoted words together.
    	    Example:
    	    
    	    >>> normalize_query('  some random  words "with   quotes  " and   spaces')
    	    ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    	
    	'''
        print findterms(query_string)
    	return [normspace(' ', (t[0] or t[1]).strip(',')) for t in findterms(query_string)] 

    def get_query(self, query_string, search_fields):
        ''' Returns a query, that is a combination of Q objects. That combination
            aims to search keywords within a model by testing the given search fields.
    
        '''
        query = None # Query to search for every search term
        terms = self.normalize_query(query_string)
        print terms
        for term in terms:
            or_query = None # Query to search for a given term in each field
            for field_name in search_fields:
                q = Q(**{"%s__icontains" % field_name: term})
                if or_query is None:
                    or_query = q
                else:
                    or_query = or_query | q
            if query is None:
                query = or_query
            else:
                query = query & or_query
        return query

    def search_for_addr(self, records, value, field):
        if field=='city':
            filtered = records.filter(
                city__startswith=value
            )
        elif field=='street':
            filtered = records.filter(
                street__startswith=value
            )
        elif field=='district':
            filtered = records.filter(
                district__startswith=value
            )
    	return filtered

    def isnumeric(self, number):
        numbers = number.split('-')
        try:
            isnum = float(numbers[-1])
        except:
            return False
        if not isnum:
            return False
        else:
            return True

    def get_addr_suggests(self, table, entered):
        suggestions = []
        entered_list = entered.split(', ')
        if len(entered_list)>1:
            street_list = entered_list[0].split(' ')
            if self.isnumeric(street_list[-1]):
                street_list.pop()
            street = ' '.join(street_list)
            city = entered_list[1]
            if len(entered_list)>2:
                district = entered_list[2][0]
            else:
                district = ''
            records = self.search_for_addr(table.objects.all(), district, 'district')
            
            records = self.search_for_addr(records, city, 'city')
            records = self.search_for_addr(records, street, 'street')
            if not records:
                records = self.search_for_addr(table.objects.all(), city, 'district')
                if not records:
                    records = self.search_for_addr(table.objects.all(), street, 'city')
                else:
                    records = self.search_for_addr(records, street, 'city')
        else:
            street_list = entered_list[0].split(' ')
            if self.isnumeric(street_list[-1]):
                street_list.pop()
            street = ' '.join(street_list)
            records = self.search_for_addr(table.objects.all(), street, 'street')
            if not records:
                records = self.search_for_addr(table.objects.all(), street, 'city')

        return records
