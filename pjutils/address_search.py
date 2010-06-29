class AddressSearch:

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

    def get_addr_suggests(self, table, entered):
        suggestions = []
        entered_list = entered.split(', ')
        if len(entered_list)>1:
            street_list = entered_list[0].split(' ')
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
        else:
            street_list = entered_list[0].split(' ')
            street_list.pop()
            street = ' '.join(street_list)
            records = self.search_for_addr(table.objects.all(), street, 'street')

        for entry in records:
            entry_string = '%s, %s, %s' %(entry.street, entry.city, entry.district)
            suggestions.append(entry_string)
        return suggestions
