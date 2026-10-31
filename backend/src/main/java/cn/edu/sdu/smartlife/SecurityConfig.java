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
 @Bean SecurityFilterChain security(HttpSecurity http,UserMapper users) throws Exception {
  return http.addFilterBefore(new org.springframework.web.filter.OncePerRequestFilter(){
 @Override protected void doFilterInternal(jakarta.servlet.http.HttpServletRequest request,jakarta.servlet.http.HttpServletResponse response,jakarta.servlet.FilterChain chain) throws java.io.IOException,jakarta.servlet.ServletException {
 var context=org.springframework.security.core.context.SecurityContextHolder.getContext();var auth=context.getAuthentication();
 if(auth!=null && auth.getDetails() instanceof Long id){var user=users.findId(id);if(user==null){context.setAuthentication(null);}else if(!user.username().equals(auth.getName())){var updated=org.springframework.security.authentication.UsernamePasswordAuthenticationToken.authenticated(user.username(),null,java.util.List.of());updated.setDetails(id);context.setAuthentication(updated);}}
 chain.doFilter(request,response);
 }
 },org.springframework.security.web.authentication.AnonymousAuthenticationFilter.class).csrf(c->c.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()).csrfTokenRequestHandler(new CsrfTokenRequestAttributeHandler()))
   .authorizeHttpRequests(a->a.requestMatchers("/error","/api/auth/**","/api/platform","/actuator/health").permitAll().anyRequest().authenticated())
   .exceptionHandling(e->e.authenticationEntryPoint((q,r,x)->r.setStatus(401)).accessDeniedHandler((q,r,x)->r.setStatus(403)))
   .logout(l->l.logoutUrl("/api/auth/logout").logoutSuccessHandler((q,r,a)->r.setStatus(204))).build();
 }
}
