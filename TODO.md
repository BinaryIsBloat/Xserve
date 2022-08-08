# Full ToDo list for Xserve #

Please expand the list if you see something important missing here. The list is also continuously updated, so please check upon it from time to time.<br>
Features that exist but that miss functionality or contain bugs have additional information inside the brackets. Working features are simply marked with OK.<br>
Features that don't exist yet and require further ellaboration also have attached information.<br>
Features marked UnKnown require further testing to determine their current state. Features which have been tested succesfully may be marked with OK, features which don't work with Broken.<br>
Features which contain known vulnerabilities should be marked with VULN URGENT and all collective ressources should be directed to fixing the issue immediately.<br>
Features which contain known vulnerabilities but are still in debug phase should be marked VULN without following URGENT, indicating that the issue may be fixed at a later point in time.<br>
A production release may only be created after all of the included features are marked OK and there is no dependency conflict.<br>

## Libraries ##

### http.py ###

 - [x] Create server initializer (OK)
    - [x] Core
    - [x] Automatic flag initialization
    - [ ] IPv6 Switch
    - [ ] UDP Support
 - [x] Create flag manager (OK, expanded continuously)
 - [x] Create connection listen function (OK)
 - [x] Create connection close function (OK)
 - [x] Create data receive function (UnKnown, Requires full port from the previously used buffer to the new robust buffer)
    - [x] Legacy core
    - [ ] Updated core
 - [ ] Create data send function (Should return data to the client)
 - [ ] Create data store function (Should store a data buffer to a file on disk)
 - [x] Create data return function (OK, may need expansion later)
 - [x] Create data whipe function (UnKnown, should clear the buffer)
