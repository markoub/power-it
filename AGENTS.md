Use Makefile commands, first to run application and then to run backend and frontend tests.
Do "make" so you can check what is in there.
Always when you modify something run these tests in the end to verify it works.
When something fails due to internet connectivity, check that call that requires internet
    - If it is some API call, use POWERIT_OFFLINE environment to return predefined result
    - If it is some npm install, or anything else that is not related to our API, please update Makefile setup part, to make sure that on the next run you fetch it all before you loose connection with the internet