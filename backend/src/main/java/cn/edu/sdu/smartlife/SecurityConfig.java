package cn.edu.sdu.smartlife;
import org.springframework.context.annotation.*;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.csrf.CookieCsrfTokenRepository;
import org.springframework.security.web.csrf.CsrfTokenRequestAttributeHandler;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
@Configuration
public class SecurityConfig {
 @Bean BCryptPasswordEncoder passwordEncoder(){return new BCryptPasswordEncoder();}
 @Bean SecurityFilterChain security(HttpSecurity http) throws Exception {
  return http.csrf(c->c.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()).csrfTokenRequestHandler(new CsrfTokenRequestAttributeHandler()))
   .authorizeHttpRequests(a->a.requestMatchers("/error","/api/auth/**","/api/platform","/actuator/health").permitAll().anyRequest().authenticated())
   .exceptionHandling(e->e.authenticationEntryPoint((q,r,x)->r.setStatus(401)).accessDeniedHandler((q,r,x)->r.setStatus(403)))
   .logout(l->l.logoutUrl("/api/auth/logout").logoutSuccessHandler((q,r,a)->r.setStatus(204))).build();
 }
}
