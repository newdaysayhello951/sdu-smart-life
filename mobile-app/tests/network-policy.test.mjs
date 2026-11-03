import {test} from 'node:test';
import assert from 'node:assert/strict';
import {normalizeServer,isApiPath,parseSse,optimizedImagePath} from '../src/network-policy.mjs';
test('production server addresses require a bare HTTPS origin',()=>{
 assert.equal(normalizeServer('https://campus.example.com/'),'https://campus.example.com');
 for(const value of ['http://campus.example.com','https://user:pass@example.com','https://example.com/api','https://example.com/?token=x','https://example.com/#x','file:///x','javascript:alert(1)'])assert.throws(()=>normalizeServer(value));
});
test('debug HTTP is restricted to LAN addresses and explicit opt-in',()=>{
 assert.throws(()=>normalizeServer('http://10.0.2.2:8080'));
 for(const value of ['http://10.0.2.2:8080','http://192.168.1.5:8080','http://172.31.0.2:8080'])assert.equal(normalizeServer(value,true),value);
 for(const value of ['http://example.com','http://172.32.0.1','http://192.168.1.5.evil.com'])assert.throws(()=>normalizeServer(value,true));
});
test('SSE parser preserves multiline data and ignores heartbeat comments',()=>{
 assert.deepEqual(parseSse('event: token\r\ndata: {"text":"海"}\r\n'),{event:'token',data:'{"text":"海"}'});
 assert.deepEqual(parseSse('data: first\ndata: second'),{event:'message',data:'first\nsecond'});
 assert.equal(parseSse(': keepalive\n'),null);
});
test('only relative campus API paths are rewritten',()=>{
 assert.equal(isApiPath('/api/products/1/image'),true);
 for(const value of ['//example.com/api/x','https://example.com/api/x','/assets/image.png','/api\\x','/api/x\r\n'])assert.equal(isApiPath(value),false);
});

test('all avatar and media routes select previews while originals stay untouched',()=>{
 assert.equal(optimizedImagePath('/api/profile/avatar?v=2'),'/api/profile/avatar?v=2&w=160');
 assert.equal(optimizedImagePath('/api/conversations/avatars/12'),'/api/conversations/avatars/12?w=160');
 assert.equal(optimizedImagePath('/api/images/product/4'),'/api/images/product/4?w=960');
 assert.equal(optimizedImagePath('/api/conversations/9/image'),'/api/conversations/9/image?w=640');
 assert.equal(optimizedImagePath('/api/conversations/9/image',true),'/api/conversations/9/image');
});
