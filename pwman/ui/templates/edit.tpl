% rebase('base.tpl')
<form action="/edit/{{node._id}}" method="POST">
Username: <input type="text" name="username" value="{{node.username}}"><br>
Password: <input type="password" name="password" value="{{node.password}}"><br>
Repeat Password: <input type="password" name="password" value="{{node.password}}"><br>
Notes: <input type="text" name="notes" value="{{node.notes}}"><br>
Tags: <input type="text" name="tags" value="{{  ', '.join([t.strip() for t in filter(None, node.tags)]) }}"><br>
 <input type="submit" value="Save edits">
</form>
