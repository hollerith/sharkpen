<script>
    function notification(message){
        var notify = Metro.notify;
        notify.setup({
            width: 300,
            duration: 1000,
            animation: 'easeOutBounce'
        });
        notify.create(message);
        notify.reset();
    }
</script>
<style>
    footer {
        position:inherit;
    }
</style>
<footer>

    <div class="bottom-nav pos-absolute">
        <button class="button">
            <span class="icon mif-plus"></span>
            <span class="label">Add</span>
        </button>
        <button class="button">
            <span class="icon mif-favorite"></span>
            <span class="label">Favorites</span>
        </button>
        <button class="button">
            <span class="icon mif-search"></span>
            <span class="label">Search</span>
        </button>
    </div>

</footer>
</body>
</html>