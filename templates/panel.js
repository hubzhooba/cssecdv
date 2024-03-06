const delPost = async (post_id) => {
	let response = await fetch(`http://localhost:8000/posts/${post_id}`, {
		method: 'DELETE'
	})
	response = await response.json();
}
const delArticle = async (article_id) => {
	let response = await fetch(`http://localhost:8000/articles/${article_id}`, {
		method: 'DELETE'
	})
	response = await response.json();
}

document.addEventListener('DOMContentLoaded', function () {
	const dropdown = document.getElementById('userDropdown');

	// Fetch usernames from the backend
	fetch('http://localhost:8000/usernames', {
		method: 'GET'
	})
		.then(response => response.json())
		.then(data => {
			console.log(data);
			// Populate the dropdown with usernames
			data.usernames.forEach(user => {
				const option = document.createElement('option');
				option.value = user; // Assuming user has an 'id' property
				option.textContent = user; // Assuming user has a 'username' property
				dropdown.appendChild(option);
			});
		})
		.catch(error => {
			console.error('Error fetching users:', error);
		});

	// Event listener for dropdown change
	dropdown.addEventListener('change', function () {
		const selectedUserName = dropdown.value;
		console.log(selectedUserName);
		fetch(`http://localhost:8000/user_id/${selectedUserName}`, {
			method: 'GET'
		}).then(response => response.json())
			.then(data => {
				const selectedUserId = data.user_id;

				fetch(`http://localhost:8000/user/${selectedUserId}/posts`, {
					method: 'GET'
				})
					.then(response => response.json())
					.then(data => {
						// Display posts on the page
						console.log(data.posts);
						const postsContainer = document.getElementById('posts');
						postsContainer.innerHTML = ''; // Clear previous posts
						data.posts.forEach(post => {
							const postCard = document.createElement('div');
							postCard.style.border = '1px solid #ccc'; // Add border for the card
							postCard.style.borderRadius = '5px'; // Add border radius for rounded corners
							postCard.style.padding = '10px'; // Add padding for spacing
							postCard.style.marginTop = '20px'; // Add margin for spacing between posts

							// Create elements for the title, content, and delete button
							const titleElement = document.createElement('h2');
							titleElement.textContent = post.title;

							const contentElement = document.createElement('p');
							contentElement.textContent = post.content;

							const deleteButton = document.createElement('button');
							deleteButton.textContent = 'Delete';
							deleteButton.style.marginTop = '5px'; // Add margin for spacing
							deleteButton.style.backgroundColor = '#ff0000'; // Change background color
							deleteButton.style.color = '#fff'; // Change text color

							// Add event listener to delete button
							deleteButton.addEventListener('click', () => {
								// Remove the post card from the DOM
								delPost(post_id); 
								window.location.reload(); 
							});

							// Append title, content, and delete button to the post card
							postCard.appendChild(titleElement);
							postCard.appendChild(contentElement);
							postCard.appendChild(deleteButton);

							// Append the post card to the posts container
							postsContainer.appendChild(postCard);
						});

						fetch(`http://localhost:8000/articles/${selectedUserId}`, {
							method: 'GET'
						})
							.then(response => response.json())
							.then(data => {
								// Display articles on the page
								console.log(data);
								const articlesContainer = document.getElementById('articles')
								articlesContainer.innerHTML = ''; // Clear previous articles
								data.forEach(article => {
									// Create a div element for the article card
									const articleCard = document.createElement('div');
									articleCard.style.border = '1px solid #ccc'; // Add border for the card
									articleCard.style.borderRadius = '5px'; // Add border radius for rounded corners
									articleCard.style.padding = '10px'; // Add padding for spacing

									// Create elements for the title, content, and delete button
									const titleElement = document.createElement('h2');
									titleElement.textContent = article.title;

									const contentElement = document.createElement('p');
									contentElement.textContent = article.content;

									const deleteButton = document.createElement('button');
									deleteButton.textContent = 'Delete';
									deleteButton.style.marginTop = '5px'; // Add margin for spacing
									deleteButton.style.backgroundColor = '#ff0000'; // Change background color
									deleteButton.style.color = '#fff'; // Change text color

									// Add event listener to delete button
									deleteButton.addEventListener('click', () => {
										// Remove the article card from the DOM
										delArticle(article.id);
										window.location.reload(); 
									});

									// Append title, content, and delete button to the article card
									articleCard.appendChild(titleElement);
									articleCard.appendChild(contentElement);
									articleCard.appendChild(deleteButton);

									// Append the article card to the articles container
									articlesContainer.appendChild(articleCard);
								});

							})
							.catch(error => {
								console.error('Error fetching articles:', error);
							});
					})
					.catch(error => {
						console.error('Error fetching posts:', error);
					});

				// Fetch articles of the selected user

			})
	});
});
