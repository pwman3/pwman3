% rebase('base.tpl')
<div class="header-container">
    <header class="wrapper clearfix">
        <h1 class="title">Pwman Web</h1>
        <nav>
            <ul>
                <li><a href="#">nav ul li a</a></li>
                <li><a href="#">nav ul li a</a></li>
                <li><a href="#">nav ul li a</a></li>
            </ul>
        </nav>
    </header>
</div>

<div class="main-container">
    <div class="main wrapper clearfix">
    <article>
    <table border="1">
        <tr><td>Username:</td> <td>{{ node.username }}</td></tr>
        <tr><td>Password:</td> <td>{{ node.password }}</td></tr>
        <tr><td>Url:</td> <td>{{node.url}} </td></tr>
        <tr><td>Notes:</td> <td>{{node.notes}}</td></tr>
        <tr><td>Tags:</td> <td>{{ ','.join((t for t in node.tags)) }}</td></tr>
    </table>
    </article>
    </div>
</div>
