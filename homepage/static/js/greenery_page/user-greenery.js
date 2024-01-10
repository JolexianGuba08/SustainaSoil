// This file contains the javascript code for the user greenery page

      function showLocationModal() {
            my_modal_5.showModal();
            my_modal_6.close();
        }
        // Function to show the registration modal
        function showRegistrationModal(location,coordinates) {
            my_modal_5.close();
            my_modal_6.showModal();
            if (location)
               $('#autocomplete-input').val(location).prop('disabled', true);
               $('#autocomplete-wrapper').data('data-coordinates' , coordinates);

        }

        function hasPackageRegistrationModal() {
            my_modal_5.close();
            my_modal_6.showModal();
            $('#autocomplete-input').hide()

        }

        function validateForm() {
            $('#registerGreeneryBttn').prop('disabled', true)
            .css('color', 'black');
            // Validate the inputs as needed
            const has_package = $('#addGreeneryButton').data("packageacc");
            const package_id = $('#package_id').val().trim();
            const packageName = $('#package_name').val().trim();
            var location = $('#autocomplete-input').val().trim();
            console.log(package_id, packageName, location)
            if (has_package === 'True'){
                location = "None";
            }
            if (package_id.trim() === '' || packageName.trim() === '' || location.trim() === '') {
                alert('All fields must be filled out');
                $('#registerGreeneryBttn').prop('disabled', false)
            }
            else{
                const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
               $.ajax({
                type: 'POST',
                url: '/check_package_id/', // Replace with your server endpoint
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                data: {
                    'package_id': package_id,
                },
                dataType: 'json',
                success: function(response) {
                   const message = response.message;
                   console.log(message)
                   if (response.status === 'True'){
                        postGreeneryData();
                   }
                   else if (response.status === 'False') {
                        alert(message);
                        $('#registerGreeneryBttn').prop('disabled', false)
                   }
                   else{
                        alert(message);
                        $('#registerGreeneryBttn').prop('disabled', false)
                   }

                },
                error: function(error) {
                     alert('Error on checking your package id');
                }
            });
            }
        }


        // Function to get the current location
        function getCurrentCoordinates() {
        $('#enableLocationBttn')
            .html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...')
            .prop('disabled', true)
            .css('color', 'black');
        return new Promise((resolve, reject) => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    position => {
                        const { latitude, longitude } = position.coords;
                        const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
                        const coor = { 'latitude': latitude, 'longitude': longitude };
                        resolve(coor);
                    },
                    error => {
                        reject(error.message);
                    }
                );
            } else {
                reject('Geolocation is not supported by your browser.');
            }
        });
        }
        function getCurrentLocation(coordinates) {
            const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
             $.ajax({
                type: 'POST',
                url: '/get_location/', // Replace with your server endpoint
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                data: coordinates,
                dataType: 'json',
                success: function(response) {
                    console.log('Location sent successfully:', response);
                    current_location = response.location;
                    showRegistrationModal(current_location,coordinates);
                },
                error: function(error) {
                    console.error('Error sending location:', error);
                }
            });
        }

        function postGreeneryData(){
            const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
            const has_package = $(this).data("packageacc");
            try {
                 var coordinates = $('#autocomplete-wrapper').data('data-coordinates')
                 var long = coordinates.longitude;
                 var lat = coordinates.latitude;
            }
            catch(err) {
                long = "None";
                lat = "None";
            }

            if (has_package === 'True'){
                long = "None";
                lat = "None";
            }
            var data = {
                'package_id': $('#package_id').val(),
                'package_name': $('#package_name').val(),
                'location': $('#autocomplete-input').val(),
                'long':long,
                'lat': lat,
            }

            $.ajax({
                type: 'POST',
                url: '/add_package/',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                data: data,
                dataType: 'json',
                success: function(response) {
                    alert('Greenery registered successfully');
                    if(response.status === 'True'){
                        window.location.href =  response.redirect_to;
                    }
                },
                error: function(error) {
                    console.error('Error on registration:', error);
                }
            });
        }
          // Event handler for the location auto input
       const inputEl = document.querySelector("#autocomplete-input");
       inputEl.addEventListener("input", onInputChange);
       getCountryData();
       let phCitiesName = [];

       async function getCountryData() {
            try {
                const phCitiesResponse = await fetch("https://ph-locations-api.buonzz.com/v1/cities");

                if (!phCitiesResponse.ok) {
                    throw new Error(`Failed to fetch city data. Status: ${phCitiesResponse.status}`);
                }

                const data = await phCitiesResponse.json();

                // Extract the array of cities from the data
                const cities = data.data;

                // Map over the array of cities and extract the names
                phCitiesName = cities.map(city => city.name);


            } catch (error) {
                console.error("Error:", error.message);
                // Handle the error as needed
                throw error;
            }
        }

           // Compare Input Value to Country Names
       function onInputChange() {
           removeAutocompleteDropdown();
           const value = inputEl.value.toLowerCase();
           if (value.length === 0) return;
           if (value === 0) return;

           const filteredNames = [];

           phCitiesName.forEach((city) => {
               if (city.substr(0, value.length).toLowerCase() === value)
                   filteredNames.push(city);
           });

           createAutocompleteDropdown(filteredNames);
       }

       // Create Dropdown
       function createAutocompleteDropdown(list) {
           const listEl = document.createElement("ul");
           listEl.className = "autocomplete-list";
           listEl.id = "autocomplete-list";

           listEl.style.maxHeight = "150px";
           listEl.style.overflow = "auto";

           list.forEach((country) => {
               const listItem = document.createElement("li");
               const countrButton = document.createElement("button");
               countrButton.innerHTML = country;
               countrButton.addEventListener("click", onCountryButtonClick);
               listItem.appendChild(countrButton);
               listEl.appendChild(listItem);
           });
           document.querySelector("#autocomplete-wrapper").appendChild(listEl);
       }

       // Remove Dropdown
       function removeAutocompleteDropdown() {
           const listEl = document.querySelector("#autocomplete-list");
           if (listEl) listEl.remove();
       }

       // Get Selected Location
       function onCountryButtonClick(e) {
           e.preventDefault();
           const buttonEl = e.target;
           inputEl.value = buttonEl.innerHTML;
           removeAutocompleteDropdown();
       }

   $(document).ready(function() {
       // Event handler for the "ADD GREENERY" button
        $('#addGreeneryButton').on('click', function(event) {
            event.preventDefault();
            const has_package = $(this).data("packageacc");
            console.log(has_package);
            if (has_package === 'True'){
                hasPackageRegistrationModal();
            }
            else{
                showLocationModal();
            }

        });

        // Add location modal
        $('#cancelLocationBttn').on('click', function(event) {
            event.preventDefault();
           showRegistrationModal();

        });
        // Event handler for the "ENABLE" button in the location modal
        $("#enableLocationBttn").click(function(e) {
            e.preventDefault(); // Prevent form submission
            getCurrentCoordinates().then(
                function (coordinates) {
                    // Handle the fulfilled promise here
                    getCurrentLocation(coordinates);
                }
            ).catch(
                function (rejectedReason) {
                    console.error('Promise rejected:', rejectedReason);
                }
            );
        });

        $('#registerGreeneryBttn').on('click', function(event) {
            event.preventDefault();
            validateForm();
        });

        $('#cancelGreeneryBttn').on('click', function(event) {
            event.preventDefault();
            my_modal_6.close();
       });




   });
