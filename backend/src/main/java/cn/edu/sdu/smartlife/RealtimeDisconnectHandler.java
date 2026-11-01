package cn.edu.sdu.smartlife;

import java.io.IOException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** A closed SSE socket is an expected disconnect; do not render JSON into the broken stream. */
@RestControllerAdvice(assignableTypes=RealtimeController.class)
class RealtimeDisconnectHandler {
 @ExceptionHandler(IOException.class) void disconnected(){}
}
