from Calendar import Calendar
cal = Calendar()
print "Purging."
cal.DeleteAll()
print "..."
cal.NewCalendar('E-6B 01', 'E-6B 01', 'VQ-3', '#1B887A', 'America/New_York')
cal.NewCalendar('E-6B 02', 'E-6B 01', 'VQ-3', '#BE6D00', 'America/New_York')
cal.NewCalendar('E-6B 03', 'E-6B 01', 'VQ-3', '#528800', 'America/New_York')
print "Done."