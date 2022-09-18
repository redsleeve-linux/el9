--- a/tests/regression/client/client.c
+++ b/tests/regression/client/client.c
@@ -29,6 +29,7 @@
 #include <sys/types.h>
 #include <sys/un.h>
 #include <unistd.h>
+#include <sys/socket.h>
 
 #include <context.h>
 #include <privkey.h>
