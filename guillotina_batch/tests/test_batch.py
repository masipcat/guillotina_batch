import json


async def test_batch_get_data(container_requester):
    """Check a value from registry."""
    async with container_requester as requester:
        await requester(
            'POST', '/db/guillotina', data=json.dumps({
                '@type': 'Item',
                'id': 'foobar1'
            }))
        await requester(
            'POST', '/db/guillotina', data=json.dumps({
                '@type': 'Item',
                'id': 'foobar2'
            }))
        response, _ = await requester(
            'POST',
            '/db/guillotina/@batch',
            data=json.dumps([{
                'method': 'GET',
                'endpoint': 'foobar1'
            }, {
                'method': 'GET',
                'endpoint': 'foobar2'
            }])
        )
        assert len(response) == 2
        assert response[1]['body']['@name'] == 'foobar2'


async def test_edit_data(container_requester):
    """Check a value from registry."""
    async with container_requester as requester:
        await requester(
            'POST', '/db/guillotina', data=json.dumps({
                '@type': 'Item',
                'id': 'foobar1'
            }))
        await requester(
            'POST', '/db/guillotina', data=json.dumps({
                '@type': 'Item',
                'id': 'foobar2'
            }))
        response, _ = await requester(
            'POST',
            '/db/guillotina/@batch',
            data=json.dumps([{
                'method': 'PATCH',
                'endpoint': 'foobar1',
                'payload': {
                    "title": "Foobar1 changed"
                }
            }, {
                'method': 'PATCH',
                'endpoint': 'foobar2',
                'payload': {
                    "title": "Foobar2 changed"
                }
            }])
        )
        response, _ = await requester(
            'POST',
            '/db/guillotina/@batch',
            data=json.dumps([{
                'method': 'GET',
                'endpoint': 'foobar1'
            }, {
                'method': 'GET',
                'endpoint': 'foobar2'
            }])
        )
        assert len(response) == 2
        assert response[0]['body']['title'] == 'Foobar1 changed'
        assert response[1]['body']['title'] == 'Foobar2 changed'


async def test_edit_sharing_data(container_requester):
    """Check a value from registry."""
    async with container_requester as requester:
        await requester(
            'POST', '/db/guillotina', data=json.dumps({
                '@type': 'Item',
                'id': 'foobar1'
            }))
        await requester(
            'POST', '/db/guillotina', data=json.dumps({
                '@type': 'Item',
                'id': 'foobar2'
            }))
        response, _ = await requester(
            'POST',
            '/db/guillotina/@batch',
            data=json.dumps([{
                'method': 'POST',
                'endpoint': 'foobar1/@sharing',
                'payload': {
                    "prinperm": [{
                        "principal": "user1",
                        "permission": "guillotina.AccessContent",
                        "setting": "AllowSingle"
                    }]
                }
            }, {
                'method': 'POST',
                'endpoint': 'foobar2/@sharing',
                'payload': {
                    "prinperm": [{
                        "principal": "user1",
                        "permission": "guillotina.AccessContent",
                        "setting": "AllowSingle"
                    }]
                }
            }])
        )
        response, _ = await requester(
            'POST',
            '/db/guillotina/@batch',
            data=json.dumps([{
                'method': 'GET',
                'endpoint': 'foobar1/@sharing'
            }, {
                'method': 'GET',
                'endpoint': 'foobar2/@sharing'
            }])
        )
        assert len(response) == 2
        assert response[0]['body']['local']['prinperm']['user1']['guillotina.AccessContent'] == 'AllowSingle'
        assert response[1]['body']['local']['prinperm']['user1']['guillotina.AccessContent'] == 'AllowSingle'


async def test_querying_permissions(container_requester):
    async with container_requester as requester:
        await requester(
            'POST', '/db/guillotina', data=json.dumps({
                '@type': 'Item',
                'id': 'foobar1'
            }))
        await requester(
            'POST', '/db/guillotina', data=json.dumps({
                '@type': 'Item',
                'id': 'foobar2'
            }))

        response, _ = await requester(
            'POST',
            '/db/guillotina/@batch',
            data=json.dumps([{
                "method": "GET",
                "endpoint": "foobar1/@canido?permission=guillotina.ChangePermissions"
            }, {
                "method": "GET",
                "endpoint": "foobar2/@canido?permission=guillotina.ChangePermissions"
            }])
        )
        assert len(response) == 2
        for resp in response:
            assert resp['status'] == 200 and resp['success']


async def test_batch_eager_commit(container_requester):
    async with container_requester as requester:
        resp, status = await requester(
            'POST',
            '/db/guillotina/@batch?eager-commit=true',
            data=json.dumps([
                {
                    'method': 'POST',
                    'endpoint': '',
                    'payload': {
                        '@type': 'Folder',
                        'id': 'folder'
                    },
                },
                {
                    'method': 'POST',
                    'payload': {
                        '@type': 'Item',
                        'id': 'item'
                    },
                    'endpoint': 'folder'
                },
                {
                    'method': 'POST',
                    'payload': {
                        '@type': 'Item',
                        'id': 'item'
                    },
                    'endpoint': 'folder'
                },
                {
                    'method': 'POST',
                    'payload': {
                        '@type': 'Item',
                        'id': 'another-item'
                    },
                    'endpoint': 'folder'
                },
                {
                    'method': 'GET',
                    'endpoint': 'folder/another-item'
                }
            ])
        )
        assert resp[0]['status'] == 201 and resp[0]['success'] is True
        assert resp[1]['status'] == 201 and resp[1]['success'] is True
        assert resp[2]['status'] == 409 and resp[2]['success'] is False
        assert resp[3]['status'] == 201 and resp[3]['success'] is True
        assert resp[4]['status'] == 200 and resp[4]['success'] is True

        resp, status = await requester(
            'GET',
            '/db/guillotina/folder',
        )
        assert status == 200

        resp, status = await requester(
            'GET',
            '/db/guillotina/folder/item',
        )
        assert status == 200
