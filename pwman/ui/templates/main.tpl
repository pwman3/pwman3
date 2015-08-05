% rebase('base.tpl')
%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)


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

                <aside>
                <h3>Select filter</h3>
                <form action="/" method="POST">
                <select multiple name="tag" onchange="this.form.submit()">
                %for tag in tags:
                <option value="{{tag}}">{{tag}}</option>
                %end
                </select>
                </form>
                </aside>
                <article>
                    <header>
                    </header>
                    <h2>Click on a username to view the details:</h2>
                    <table border="1">
                    %for node in nodes:
                    <tr>
                      <td><a href=/node/{{node._id}}>{{node.username}}@{{node.url}}</a></td>
                      <td>{{  ', '.join([t.strip() for t in filter(None, node.tags)]) }}</td>
                      <td><a href=/edit/{{node._id}}>edit</a></td>
                      </tr>
                    %end
                    </table>
                </article>


            </div> <!-- #main -->
        </div> <!-- #main-container -->
        <div class="footer-container">
        <div class="forget-button">
        <form action="/forget" method="POST">
        <input type="submit" value="Forget password">
        </form>
        </div>
        </div>
        <script src="static/js/vendor/jquery-1.11.0.js"></script>
        <script src="static/js/plugins.js"></script>
        <script src="static/js/main.js"></script>
