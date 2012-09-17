from Calendar import Calendar
import apiclient.errors

cal = Calendar()
# cal.PrintOwnCalendars()
# print "\n"

print "Purging."
cal.DeleteAll()
print "..."

try:
    cal.NewCalendar('E-6B 01', 'E-6B 01', 'VQ-3', '#1B887A')
    cal.NewCalendar('E-6B 02', 'E-6B 02', 'VQ-3', '#BE6D00')
    cal.NewCalendar('E-6B 03', 'E-6B 03', 'VQ-3', '#528800')

except apiclient.errors.HttpError as e:
    print e.__str__()

    
print "Done."