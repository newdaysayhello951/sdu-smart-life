package cn.edu.sdu.smartlife;
import java.security.Principal;
import java.math.BigDecimal;
import java.util.*;
import org.apache.ibatis.annotations.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;
@RestController
@RequestMapping("/api/orders")
public class OrderController {
 private final OrderMapper db;private final UserMapper users;
 public OrderController(OrderMapper db,UserMapper users){this.db=db;this.users=users;}
 public record Order(long id,long productId,String title,BigDecimal price,String status,String buyer,String seller,String role,String createdAt){}
 @GetMapping public List<Order> mine(Principal p,@RequestParam(defaultValue="0") long before){if(before<0)throw new ResponseStatusException(HttpStatus.BAD_REQUEST);return db.mine(users.find(p.getName()).id(),before);}
 @PostMapping("/product/{id}") @org.springframework.transaction.annotation.Transactional
 public Map<String,Long> reserve(@PathVariable long id,Principal p){
 long buyer=users.find(p.getName()).id();var product=db.lockProduct(id);if(product==null)throw new ResponseStatusException(HttpStatus.NOT_FOUND);
 if(product.ownerId()==null)throw new ResponseStatusException(HttpStatus.CONFLICT,"历史商品卖家尚未确认，暂不可交易");
 if(product.ownerId()==buyer)throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"不能购买自己的商品");
 if(!product.status().equals("AVAILABLE")){Long previous=db.active(id,buyer);if(previous!=null&&product.status().equals("RESERVED"))return Map.of("id",previous);throw new ResponseStatusException(HttpStatus.CONFLICT,"商品已被预订或不可交易");}
 if(db.reserve(id)!=1)throw new ResponseStatusException(HttpStatus.CONFLICT);
 db.create(id,buyer,product.ownerId(),product.title(),product.price());return Map.of("id",db.last());
 }
 @PostMapping("/{id}/cancel") @org.springframework.transaction.annotation.Transactional public void cancel(@PathVariable long id,Principal p){change(id,p,false);}
 @PostMapping("/{id}/complete") @org.springframework.transaction.annotation.Transactional public void complete(@PathVariable long id,Principal p){change(id,p,true);}
 private void change(long id,Principal p,boolean complete){
 var initial=db.order(id);if(initial==null)throw new ResponseStatusException(HttpStatus.NOT_FOUND);
 db.lockProduct(initial.productId());var order=db.lockOrder(id);long user=users.find(p.getName()).id();
 if(user!=order.buyerId()&&user!=order.sellerId())throw new ResponseStatusException(HttpStatus.NOT_FOUND);
 if(complete&&user!=order.buyerId())throw new ResponseStatusException(HttpStatus.FORBIDDEN,"仅买家可确认收货");
 String next=complete?"COMPLETED":"CANCELLED";if(order.status().equals(next))return;
 if(!order.status().equals("RESERVED"))throw new ResponseStatusException(HttpStatus.CONFLICT,"订单状态已变化");
 db.state(id,next);if(db.productState(order.productId(),complete?"SOLD":"AVAILABLE")!=1)throw new ResponseStatusException(HttpStatus.CONFLICT);
 }
}
@Mapper
interface OrderMapper {
 record Product(long id,Long ownerId,String title,BigDecimal price,String status){}
 record StoredOrder(long id,long productId,long buyerId,long sellerId,String status){}
 @Select("SELECT id,owner_id AS ownerId,title,price,status FROM product WHERE id=#{id} FOR UPDATE") Product lockProduct(long id);
 @Select("SELECT id FROM trade_order WHERE product_id=#{id} AND buyer_id=#{buyer} AND status='RESERVED' ORDER BY id DESC LIMIT 1") Long active(@Param("id")long id,@Param("buyer")long buyer);
 @Update("UPDATE product SET status='RESERVED' WHERE id=#{id} AND status='AVAILABLE'") int reserve(long id);
 @Insert("INSERT INTO trade_order(product_id,buyer_id,seller_id,product_title,price) VALUES(#{id},#{buyer},#{seller},#{title},#{price})") void create(@Param("id")long id,@Param("buyer")long buyer,@Param("seller")long seller,@Param("title")String title,@Param("price")BigDecimal price);
 @Select("SELECT LAST_INSERT_ID()") long last();
 @Select("SELECT id,product_id AS productId,buyer_id AS buyerId,seller_id AS sellerId,status FROM trade_order WHERE id=#{id}") StoredOrder order(long id);
 @Select("SELECT id,product_id AS productId,buyer_id AS buyerId,seller_id AS sellerId,status FROM trade_order WHERE id=#{id} FOR UPDATE") StoredOrder lockOrder(long id);
 @Update("UPDATE trade_order SET status=#{status} WHERE id=#{id}") void state(@Param("id")long id,@Param("status")String status);
 @Update("UPDATE product SET status=#{status} WHERE id=#{id} AND status='RESERVED'") int productState(@Param("id")long id,@Param("status")String status);
 @Select("SELECT o.id,o.product_id AS productId,o.product_title AS title,o.price,o.status,b.username AS buyer,s.username AS seller,CASE WHEN o.buyer_id=#{user} THEN 'BUYER' ELSE 'SELLER' END AS role,CAST(o.created_at AS CHAR) AS createdAt FROM trade_order o JOIN app_user b ON b.id=o.buyer_id JOIN app_user s ON s.id=o.seller_id WHERE (o.buyer_id=#{user} OR o.seller_id=#{user}) AND (#{before}=0 OR o.id<#{before}) ORDER BY o.id DESC LIMIT 30") List<OrderController.Order> mine(@Param("user")long user,@Param("before")long before);
}
